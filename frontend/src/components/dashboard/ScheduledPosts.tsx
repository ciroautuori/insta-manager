import React from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import { Link } from 'react-router-dom'
import { 
  Calendar, 
  Clock, 
  Image, 
  FileText, 
  Video,
  ExternalLink,
  ImageIcon
} from 'lucide-react'
import { format } from 'date-fns'
import { it } from 'date-fns/locale'

interface ScheduledPost {
  id: string
  account_username: string
  account_avatar?: string
  post_type: 'feed' | 'story' | 'reel'
  content: string
  media_files: string[]
  scheduled_time: string
  status: 'pending' | 'processing' | 'failed' | 'completed'
  retry_count: number
}

interface ScheduledPostsProps {
  posts: ScheduledPost[]
  className?: string
}

const getPostTypeIcon = (type: string) => {
  switch (type) {
    case 'story':
      return ImageIcon
    case 'reel':
      return Video
    default:
      return FileText
  }
}

const getStatusColor = (status: string) => {
  switch (status) {
    case 'completed':
      return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300'
    case 'processing':
      return 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-300'
    case 'failed':
      return 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-300'
    default:
      return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-300'
  }
}

const getStatusLabel = (status: string) => {
  switch (status) {
    case 'completed':
      return 'Pubblicato'
    case 'processing':
      return 'In corso'
    case 'failed':
      return 'Fallito'
    default:
      return 'In attesa'
  }
}

const ScheduledPosts: React.FC<ScheduledPostsProps> = ({ posts, className }) => {
  const upcomingPosts = posts
    .filter(post => post.status === 'pending' && new Date(post.scheduled_time) > new Date())
    .sort((a, b) => new Date(a.scheduled_time).getTime() - new Date(b.scheduled_time).getTime())

  if (!upcomingPosts.length) {
    return (
      <Card className={className}>
        <CardHeader>
          <CardTitle>Post Programmati</CardTitle>
          <CardDescription>Nessun post programmato</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="text-center py-6 text-muted-foreground">
            <Calendar className="mx-auto h-12 w-12 mb-4 opacity-50" />
            <p>Nessun post in programma</p>
            <Button variant="outline" className="mt-4" asChild>
              <Link to="/scheduled">Programma Post</Link>
            </Button>
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card className={className}>
      <CardHeader className="flex flex-row items-center justify-between">
        <div>
          <CardTitle>Post Programmati</CardTitle>
          <CardDescription>
            {upcomingPosts.length} post in programma
          </CardDescription>
        </div>
        <Button variant="outline" size="sm" asChild>
          <Link to="/scheduled">
            Visualizza Calendario
            <ExternalLink className="ml-2 h-4 w-4" />
          </Link>
        </Button>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {upcomingPosts.slice(0, 5).map((post) => {
            const PostIcon = getPostTypeIcon(post.post_type)
            const isToday = format(new Date(post.scheduled_time), 'yyyy-MM-dd') === 
                           format(new Date(), 'yyyy-MM-dd')
            const isSoon = new Date(post.scheduled_time).getTime() - new Date().getTime() < 3600000 // 1 hour

            return (
              <div key={post.id} className="flex items-start space-x-4 p-4 border rounded-lg">
                <div className="flex-shrink-0">
                  <div className="relative">
                    <Avatar className="h-10 w-10">
                      <AvatarImage src={post.account_avatar} />
                      <AvatarFallback>
                        {post.account_username.charAt(0).toUpperCase()}
                      </AvatarFallback>
                    </Avatar>
                    <div className="absolute -bottom-1 -right-1 h-6 w-6 bg-background border-2 border-background rounded-full flex items-center justify-center">
                      <PostIcon className="h-3 w-3 text-muted-foreground" />
                    </div>
                  </div>
                </div>

                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center space-x-2">
                      <span className="font-medium text-sm">@{post.account_username}</span>
                      <Badge variant="secondary" className="text-xs capitalize">
                        {post.post_type}
                      </Badge>
                      {isSoon && (
                        <Badge className="text-xs bg-orange-100 text-orange-800">
                          Presto
                        </Badge>
                      )}
                    </div>
                    <Badge 
                      variant="secondary" 
                      className={`text-xs ${getStatusColor(post.status)}`}
                    >
                      {getStatusLabel(post.status)}
                    </Badge>
                  </div>

                  <p className="text-sm text-muted-foreground mb-2 line-clamp-2">
                    {post.content.length > 100 
                      ? `${post.content.substring(0, 100)}...` 
                      : post.content
                    }
                  </p>

                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-4 text-xs text-muted-foreground">
                      <div className="flex items-center space-x-1">
                        <Clock className="h-3 w-3" />
                        <span>
                          {format(new Date(post.scheduled_time), 
                            isToday ? 'HH:mm' : 'dd MMM, HH:mm', 
                            { locale: it }
                          )}
                        </span>
                      </div>
                      {post.media_files.length > 0 && (
                        <div className="flex items-center space-x-1">
                          <Image className="h-3 w-3" />
                          <span>{post.media_files.length} media</span>
                        </div>
                      )}
                    </div>

                    <div className="flex items-center space-x-1">
                      {post.retry_count > 0 && (
                        <Badge variant="outline" className="text-xs">
                          Retry: {post.retry_count}
                        </Badge>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            )
          })}

          {upcomingPosts.length > 5 && (
            <div className="text-center pt-4 border-t">
              <Button variant="ghost" asChild>
                <Link to="/scheduled">
                  Visualizza tutti i {upcomingPosts.length} post programmati
                </Link>
              </Button>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  )
}

export default ScheduledPosts
